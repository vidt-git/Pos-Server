# Product Icons

Add your product icons to this folder.

## Current Products

- **todo-icon.png** - Icon for the Todo App (add this file)

## Adding New Products

1. Add your icon image to this folder (recommended size: 512x512px or larger, PNG/SVG format)
2. Update `templates/home.html` by copying the product card template
3. Update the icon path, link URL, and product name

Example:
```html
<a href="/your-product-url" class="product-card">
    <div class="product-icon">
        <img src="{{ url_for('static', path='/assets/icons/your-icon.png') }}" alt="Your Product">
    </div>
    <h2 class="product-name">Your Product</h2>
</a>
```

## Icon Guidelines

- Use square icons (1:1 aspect ratio)
- Recommended size: 512x512px or larger
- Formats: PNG with transparency or SVG
- Keep file sizes reasonable (< 500KB)
