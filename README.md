# Not Dead Yet!
[![pypi-badge][]][pypi] 

[pypi-badge]: https://img.shields.io/pypi/v/not-dead-yet
[pypi]: https://pypi.org/project/not-dead-yet

`not_dead_yet` is a stupid simple web server, which provides a live-server over HTML files. 
If any files in the given directory are modified, loaded HTML pages will refresh.

## Usage
Launch a live server on `localhost:8080` with 
```bash
ndy serve .
```

Some users may prefer to use a more advanced change-detection routine than the simple polling API. External watchers can be used with `not-dead-yet` by disabling the file-watching feature, and triggering a reload over the TCP socket:
```bash
# Launch server
ndy serve --no-watch &

# Watch for changes, and call `ndy reload` when required
watchexec -w . -- ndy reload
```
