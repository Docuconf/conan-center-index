#include <iostream>

#include <docuconf/docuconf.hpp>

int main(int argc, char** argv) {
    CLI::App app{"test_package"};
    docuconf::Declaration config{app, "test-package"};

    int port = 0;
    config.add_var("PORT", port, "HTTP listen port").range(1, 65535).default_val(8080);

    DOCUCONF_PARSE(config, argc, argv);
    std::cout << "port " << port << "\n";
    return 0;
}
