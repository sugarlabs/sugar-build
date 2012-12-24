import os
import subprocess
import tempfile

upload_host = "shell.sugarlabs.org"
upload_root = "/upload/sources/sucrose/glucose"
download_uri = "http://download.sugarlabs.org/sources/sucrose/glucose"
announce_to = "sugar-devel@lists.sugarlabs.org"

def exists(module, filename):
    release_path = os.path.join(upload_root, module.name, filename)
    result = subprocess.call(["ssh", upload_host, "test", "-f", release_path])
    return result == 0

def upload(module, path):
    upload_path = os.path.join(upload_root, module.name)
    upload_dest = "%s:%s" % (upload_host, upload_path)
    return subprocess.call(["scp", path, upload_dest]) == 0

def announce(module, filename, version, annotation):
    fd, announce_path = tempfile.mkstemp("announce-")

    with os.fdopen(fd, "w") as f:
        f.write("From: %s\n" % _get_email())
        f.write("To: %s\n" % announce_to)
        f.write("Subject: [RELEASE] %s-%s\n" % (module.name, version))

        f.write("\n%s\n" % annotation)
        f.write("== Source ==\n\n")
        f.write("%s/%s/%s" % (download_uri, module.name, filename))

    result = False

    upload_dest = "%s:~" % upload_host
    if subprocess.call(["scp", announce_path, upload_dest]) == 0:
        if subprocess.call(["ssh", upload_host, "sendmail", "-t",
                            "<", os.path.basename(announce_path)]):
            result = True

    os.unlink(announce_path)

    return result

def _get_email():
    return subprocess.check_output(['git', 'config', 'user.email']).strip()
