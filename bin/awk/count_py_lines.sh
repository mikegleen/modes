find src -type f -exec wc -l {} \; | awk '/\.py/{total += $1} END{print total}'

