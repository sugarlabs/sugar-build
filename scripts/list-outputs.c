#include <stdio.h>
#include <X11/extensions/Xrandr.h>

int main(int argc, char **argv)
{
    Display *dpy = XOpenDisplay(NULL);
    XRRScreenResources *rr;
    XRROutputInfo *output;
    int i;

    XSynchronize(dpy, 1);

    rr = XRRGetScreenResources(dpy, DefaultRootWindow(dpy));

    if (rr != NULL) {
        for (i = 0; i < rr->noutput; i++) {
            output = XRRGetOutputInfo(dpy, rr, rr->outputs[i]);

            if (output->connection == RR_Connected) {
                printf("%s\n", output->name);
            }

            XRRFreeOutputInfo(output);
        }
    }

    XRRFreeScreenResources(rr);

    XSync(dpy, 1);
    XCloseDisplay(dpy);

    return 0;
}
