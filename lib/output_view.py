import sublime


###----------------------------------------------------------------------------


def find_view(window, title, current_view=None):
    """
    Attempt to find a view with the given title (name) in the given window
    """
    if current_view is not None and current_view.name() == title:
        return current_view

    for view in window.views():
        if view.name() == title:
            return view


def new_scratch_view(window, title, syntax=None):
    """
    Create a new view in the given window, giving it a name and an optional
    syntax.
    """
    view = window.new_file()
    view.set_scratch(True)
    view.set_name(title)

    if syntax is not None:
        view.assign_syntax(syntax)

    return view


def clear_view(view):
    """
    Clear view contents entirely. Also returns it to single selection.
    """
    view.sel().clear()
    view.sel().add(sublime.Region(0, view.size()))
    view.run_command("left_delete")


def _save_state(view):
    """
    Save ths current size, selection and viewport position for the provided
    view.
    """
    return (view.size(), list(view.sel()), view.viewport_position())


def _restore_state(view, state):
    """
    Restore the selection and viewport position that was previously saved via
    _save_state(). If the last selection was at the end of the buffer, put it
    back there even if the size of the buffer has changed so that future append
    operations will work.
    """
    size = state[0]
    sel = state[1]
    vpos = state[2]

    # If the last selection was at the end of the buffer, replace that
    # selection with the new end of the buffer so the relative position remains
    # the same.
    if sublime.Region(size, size) == sel[-1]:
        sel[-1] = sublime.Region(view.size(), view.size())

    view.sel().clear()
    for region in sel:
        view.sel().add(region)

    view.set_viewport_position(vpos, False)


def output_to_view(window,
                   title,
                   content,
                   reuse=True,
                   clear=True,
                   syntax=None,
                   settings=None,
                   current_view=None):
    """
    Add the content provided to a view in the given window, which has the title
    provided. This will create a new view unless one with the title provided
    already exists and resuse is true. In the latter case current_view is
    checked first to see if it is the appropriate view before scanning, so that
    multiple views with the same title can be distinguished by the caller.

    If an existing view is used, clear indicates if the current content should
    be cleared or not before adding the new data.

    When a new view is created, the optional syntax and settings will be
    applied to the newly created view; when a view is reused, it is assumed
    that these have already been set up.

    The text will be appended to the end of the buffer. Care is taken to ensure
    that the cursor position, view position and selection are maintained when
    this is invoked.

    This call leaves the output view in a read-only state; it is not neccesary
    to turn this off if you invoke this method a second time and reuse a view.
    """

    if not isinstance(content, str):
        content = "\n".join(content)

    view = find_view(window, title, current_view) if (reuse) else None

    if view is None:
        view = new_scratch_view(window, title, syntax)
    else:
        view.set_read_only(False)

        if clear is True:
            clear_view(view)

        if window.active_view() != view:
            window.focus_view(view)

    if settings is not None:
        for setting in settings:
            view.settings().set(setting, settings[setting])

    state = _save_state(view)
    view.run_command("append", {"characters": content})
    _restore_state(view, state)

    view.set_read_only(True)

    return view


###----------------------------------------------------------------------------
