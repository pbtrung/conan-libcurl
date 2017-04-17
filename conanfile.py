import os

from conans import CMake, ConanFile
from conans.tools import download, unzip, replace_in_file


class LibcurlConan(ConanFile):
    name = "libcurl"
    version = "7.53.1"
    zip_dir = "curl-%s" % version
    url = "https://github.com/pbtrung/conan-libcurl"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    license="https://curl.haxx.se/docs/copyright.html"
    default_options = "shared=False"
    generators = "cmake"
    exports = ["CMakeLists.txt", "FindCURL.cmake"]
    description = "libcurl - the multiprotocol file transfer library"

    def source(self):
        zip_name = "curl-%s.tar.gz" % self.version
        download("https://curl.haxx.se/download/%s" % zip_name, zip_name, verify=False)
        unzip(zip_name)
        os.unlink(zip_name)
        download("https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=False)

    def configure(self):
        self.requires.add("zlib/1.2.11@lasote/stable", private=False)
        self.requires.add("libnghttp2/1.21.1@pbtrung/stable", private=False)
        self.requires.add("OpenSSL/1.0.2k@lasote/stable", private=False)

    def config_options(self):
        self.options["OpenSSL"].shared = self.options.shared
        self.options["libnghttp2"].shared = self.options.shared
        self.options["zlib"].shared = self.options.shared

    def build(self):
        conan_magic_lines = '''project(CURL)
cmake_minimum_required(VERSION 3.0)
include(../conanbuildinfo.cmake)
CONAN_BASIC_SETUP()
'''
        replace_in_file("%s/CMakeLists.txt" % self.zip_dir, "cmake_minimum_required(VERSION 2.8 FATAL_ERROR)", conan_magic_lines)
        replace_in_file("%s/CMakeLists.txt" % self.zip_dir, "project( CURL C )", "")
        replace_in_file("%s/CMakeLists.txt" % self.zip_dir, "include(CurlSymbolHiding)", "")

        replace_in_file("%s/src/CMakeLists.txt" % self.zip_dir, "add_executable(", "IF(0)\n add_executable(")
        replace_in_file("%s/src/CMakeLists.txt" % self.zip_dir, "install(TARGETS ${EXE_NAME} DESTINATION bin)", "ENDIF()") # EOF
        cmake = CMake(self.settings)
        static = "-DBUILD_SHARED_LIBS=ON -DCURL_STATICLIB=OFF" if self.options.shared else "-DBUILD_SHARED_LIBS=OFF -DCURL_STATICLIB=ON"
        http2 = "-DUSE_NGHTTP2=ON"
        self.run("cd %s && mkdir _build" % self.zip_dir)
        cd_build = "cd %s/_build" % self.zip_dir
        self.run('%s && cmake .. %s -DBUILD_TESTING=OFF %s %s' % (cd_build, cmake.command_line, static, http2))
        self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))

    def package(self):
        # Copy findZLIB.cmake to package
        self.copy("FindCURL.cmake", ".", ".")

        # Copying zlib.h, zutil.h, zconf.h
        self.copy("*.h", "include/curl", "%s" % (self.zip_dir), keep_path=False)

        # Copy the certs to be used by client
        self.copy(pattern="cacert.pem", keep_path=False)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="lib", src=self.zip_dir, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self.zip_dir, keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", src=self.zip_dir, keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src=self.zip_dir, keep_path=False)

    def package_info(self):
        if self.settings.os != "Windows":
            self.cpp_info.libs = ['curl']
        else:
            self.cpp_info.libs = ['libcurl']