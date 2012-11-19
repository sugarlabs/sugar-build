#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>

int main(int argc, char **argv)
{
    Display *display = XOpenDisplay(NULL);
    Window window, root_window;
    Atom atom;
    int width = 100, height = 100;

    if (argc > 1) {
        char *geometry = strdup(argv[1]);
        char *delimiter = strchr(geometry, 'x');

        if (delimiter == NULL) {
            fprintf(stderr, "Cannot parse geometry\n");
            free(geometry);
            exit(1);
        }

        *delimiter = '\0';
        width = atoi(geometry);
        height = atoi(delimiter + 1);

        free(geometry);
    }

    root_window = RootWindow(display, 0);

    window = XCreateSimpleWindow(display, root_window, 0, 0,
                                 width, height, 0, 0, 0);

    printf("%d\n", window);
    fflush(stdout);

    if (argc < 2) {
        atom = XInternAtom(display, "_NET_WM_STATE_FULLSCREEN", True);
        XChangeProperty(display, window,
                        XInternAtom(display, "_NET_WM_STATE", True),
                        XA_ATOM, 32, PropModeReplace,
                        (unsigned char *)&atom, 1);
    }

    XMapWindow(display, window);

    XFlush(display);

    while(1) {
        sleep(60);
    }

    XCloseDisplay(display);

    return(0);
}
