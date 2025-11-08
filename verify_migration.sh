#!/bin/bash

echo "🔍 Verifying Modular Structure Migration..."
echo ""

# Check if new index.html exists
if [ -f "index.html" ]; then
    SIZE=$(wc -c < index.html)
    LINES=$(wc -l < index.html)
    echo "✅ index.html exists (${SIZE} bytes, ${LINES} lines)"
else
    echo "❌ index.html not found"
    exit 1
fi

# Check if backup exists
if [ -f "index_old_backup.html" ]; then
    SIZE=$(wc -c < index_old_backup.html)
    echo "✅ Backup exists: index_old_backup.html (${SIZE} bytes)"
else
    echo "⚠️  No backup found"
fi

# Check templates
echo ""
echo "📁 Checking templates..."
TEMPLATES=(
    "templates/components/head.html"
    "templates/components/sidebar.html"
    "templates/components/modals.html"
    "templates/pages/dashboard.html"
)

for template in "${TEMPLATES[@]}"; do
    if [ -f "$template" ]; then
        echo "  ✅ $template"
    else
        echo "  ❌ $template MISSING"
    fi
done

# Check JavaScript modules
echo ""
echo "📜 Checking JavaScript modules..."
JS_FILES=(
    "static/js/navigation.js"
    "static/js/dashboard.js"
    "static/js/fileManager.js"
    "static/js/componentLoader.js"
    "static/js/calendar.js"
    "static/js/chat.js"
    "static/js/quiz.js"
    "static/js/analytics.js"
)

for js in "${JS_FILES[@]}"; do
    if [ -f "$js" ]; then
        echo "  ✅ $js"
    else
        echo "  ❌ $js MISSING"
    fi
done

# Check CSS
echo ""
echo "🎨 Checking CSS files..."
CSS_FILES=(
    "static/css/style.css"
    "static/css/components.css"
)

for css in "${CSS_FILES[@]}"; do
    if [ -f "$css" ]; then
        SIZE=$(wc -c < "$css")
        echo "  ✅ $css (${SIZE} bytes)"
    else
        echo "  ❌ $css MISSING"
    fi
done

echo ""
echo "✨ Migration verification complete!"
echo ""
echo "Next steps:"
echo "1. Start server: python main.py"
echo "2. Visit: http://localhost:5000"
echo "3. Test all features"
echo "4. If everything works, delete backup files"
echo ""
