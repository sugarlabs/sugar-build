#include <stdio.h>
#include <X11/extensions/Xrandr.h>

int main(int argc, char **argv)
{
    int port;

    for (port = 99; port < 1000; port++) {
        char display_name[255];

        sprintf(display_name, ":%d", port);
        Display *dpy = XOpenDisplay(display_name);

        if (!dpy) {
            printf(display_name);
            return 0;
        } else {
            XCloseDisplay(dpy);
        }
    }

    printf("No free display found");

    return 0;
}
