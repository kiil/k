rm -r docs
cd congo
HUGO_ENV=production hugo --ignoreCache
cd -
git add .
git commit --message $'"(input `message: `)"'
git push
