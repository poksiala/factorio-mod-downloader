from .dependencies import solve_dependencies


if __name__ == "__main__":
    with open("modlist", "r") as f:
        mods = solve_dependencies(f.readlines())
        for mod in mods:
            print(mod)
