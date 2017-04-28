from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(args="--build missing")
    builder.add_common_builds(pure_c=True, shared_option_name="libcurl:shared")
    builder.run()
