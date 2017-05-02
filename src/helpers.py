import sublime


###----------------------------------------------------------------------------


def find_override(view, pkg_name, override):
    """
    Given a report view, return the bounds of the override belonging to the
    given package. Returns None if the position cannot be located.
    """
    if not view.match_selector(0, "text.override-audit"):
        return None

    bounds = None
    packages = view.find_by_selector("entity.name.package")
    for index, pkg_pos in enumerate(packages):
        if view.substr(pkg_pos) == pkg_name:
            end_pos = view.size()
            if index + 1 < len(packages):
                end_pos = packages[index + 1].begin() - 1

            bounds = sublime.Region(pkg_pos.end() + 1, end_pos)
            break

    if bounds is None:
        return

    overrides = view.find_by_selector("entity.name.filename.override")
    for file_pos in overrides:
        if bounds.contains(file_pos) and view.substr(file_pos) == override:
            return file_pos

    return None


###----------------------------------------------------------------------------
