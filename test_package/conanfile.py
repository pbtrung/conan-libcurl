from conans.model.conan_file import ConanFile
from conans import CMake
import os

############### CONFIGURE THESE VALUES ##################
default_user = "pbtrung"
default_channel = "stable"
#########################################################

channel = os.getenv("CONAN_CHANNEL", default_channel)
username = os.getenv("CONAN_USERNAME", default_user)

class DefaultNameConan(ConanFile):
    version = "7.54.0"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    requires = "libcurl/%s@%s/%s" % (version, username, channel)

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake %s %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="lib")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        self.copy(pattern="*cacert*", dst="bin")

    def test(self):
        self.run("cd bin && .%sexample" % os.sep)
