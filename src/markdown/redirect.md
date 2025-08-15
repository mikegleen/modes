
## Redirect stderr to stdout

This will redirect the stderr (which is descriptor 2) to the file descriptor 1 which is the the stdout.

```bash
2>&1
```

## Redirect stdout  to File

Now when perform this you are redirecting the stdout to the file `sample.s`

```bash
myprogram > sample.s
```

## Redirect stderr and stdout to File

Combining the two commands will result in redirecting both stderr and stdout to sample.s

```bash
myprogram > sample.s 2>&1
```

## Redirect stderr and stdout to /dev/null

Redirect to `/dev/null` if you want to completely silent your application.

```bash
myprogram >/dev/null 2>&1
```
