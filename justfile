build:
    mkdir -p dist
    cp src/images/* src/style.css dist/
    for file in src/pages/*.md; do \
        pandoc "$file" \
            --output "dist/$(basename "$file" .md).html" \
            --standalone \
            --syntax-highlighting default \
            --template=src/template.html; \
    done

dev:
    wrangler dev --live-reload
