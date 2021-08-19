#!/usr/bin/env bash
# Very simple script that tries to scrap licences from dependencies.

# Complete list of our dependencies
GOSUM="$(dirname "$0")/../go.sum"

get_licence_on_github() {
  repo="$1"
  licence_object=$(curl -s -L "https://$GITHUB_TOKEN:x-oauth-basic@api.github.com/repos/${repo}/license")
  licence_url=$(echo "${licence_object}" | jq -r .download_url)
  licence_name=$(echo "${licence_object}" | jq -r .license.name)

  echo "Name: ${licence_name}"
  echo "Content:"
  curl --fail -s -L "${licence_url}"
}

get_licence_on_golang() {
  repo="$1"

  licence_object=$(curl -s -L "https://pkg.go.dev/${repo}?tab=licenses")
  licence_content=$(echo "${licence_object}" | grep "License-contents" | sed -n 's|<pre class="License-contents">\(.*\)</pre>|\1|p')
  licence_name=$(echo "${licence_object}" | grep 'id="#lic-0"' | sed -n 's|<h2><div.*>\(.*\)</div></h2>|\1|p')

  echo "Name: ${licence_name}"
  echo "Content: ${licence_content}"
}

cut -d ' ' -f 1 "${GOSUM}" | sort -u | while read -r dep; do

  echo "License for ${dep}:"

  if [[ ${dep} == "github.com"* ]]; then
    if ! get_licence_on_github "${dep#github.com/}"; then
      echo "NOT FOUND"
    fi
  elif [[ ${dep} == "golang.org"* ]]; then
    if ! get_licence_on_golang "${dep}"; then
      echo "NOT FOUND"
    fi
  else
    echo "NOT SUPPORTED"
  fi

  echo "============="
  echo ""
done
