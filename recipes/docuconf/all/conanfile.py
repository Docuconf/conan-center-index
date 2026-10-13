from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.0.9"


class DocuconfConan(ConanFile):
    name = "docuconf"
    description = ("Typed configuration contracts for CLI11: declare a service's configuration once, check "
                   "environment variables and mounted files at startup, and export a CUE contract for the platform.")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docuconf.dev/languages/cpp/"
    topics = ("configuration", "environment-variables", "kubernetes", "cli11", "cue")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_file_inputs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_file_inputs": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # The public headers include CLI11 and nlohmann/json.
        self.requires("cli11/2.7.2", transitive_headers=True)
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        self.requires("re2/20230301")
        self.requires("json-schema-validator/2.4.0")
        if self.options.with_file_inputs:
            self.requires("openssl/[>=3 <4]")
            self.requires("yaml-cpp/0.8.0")
            self.requires("tomlplusplus/3.4.0")

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not export symbols for a DLL; build it static with msvc.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["DOCUCONF_FETCH_DEPS"] = False
        tc.cache_variables["DOCUCONF_INSTALL"] = True
        tc.cache_variables["DOCUCONF_BUILD_TESTS"] = False
        tc.cache_variables["DOCUCONF_BUILD_EXAMPLES"] = False
        tc.cache_variables["DOCUCONF_FILE_INPUTS"] = bool(self.options.with_file_inputs)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["docuconf"]
        self.cpp_info.set_property("cmake_file_name", "docuconf")
        self.cpp_info.set_property("cmake_target_name", "docuconf::docuconf")
        self.cpp_info.defines = [f"DOCUCONF_FILE_INPUTS={1 if self.options.with_file_inputs else 0}"]
        self.cpp_info.requires = [
            "cli11::cli11",
            "nlohmann_json::nlohmann_json",
            "re2::re2",
            "json-schema-validator::json-schema-validator",
        ]
        if self.options.with_file_inputs:
            self.cpp_info.requires += ["openssl::ssl", "openssl::crypto", "yaml-cpp::yaml-cpp",
                                       "tomlplusplus::tomlplusplus"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
