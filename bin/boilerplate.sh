SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
green () {
    print -P "%F{green}$*%f"
}
yellow () {
    print -P "%F{yellow}$*%f"
}
