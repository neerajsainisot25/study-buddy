# 🚀 Start Server Guide

## Quick Start

### 1. Start the Server
```bash
python main.py
```

The server will automatically find an available port (usually 5000, 5001, 5002, or 5003).

### 2. Open in Browser
Look for this line in the terminal output:
```
🌐 Access the app at: http://localhost:XXXX
```

Open that URL in your browser.

### 3. What You Should See
- ✅ Sidebar with navigation (Dashboard, Chat, Quiz, Calendar, Analytics, Profile)
- ✅ Dashboard page with metrics and quick actions
- ✅ Welcome message: "Welcome back, Alex! 👋"
- ✅ Study streak, personal best, and quiz metrics
- ✅ Quick action buttons (Start Chat, Create Quiz, Add Files, View Calendar)

## Troubleshooting

### Blank Page or Missing Content

**Problem**: Page loads but nothing is visible

**Solution**:
1. Open browser DevTools (F12 or Right-click → Inspect)
2. Check the Console tab for errors
3. Look for failed network requests in the Network tab

Common issues:
- CSS not loading → Check `/static/css/style.css` loads successfully
- Components not loading → Check `/templates/components/sidebar.html` loads
- JavaScript errors → Check all `.js` files in `/static/js/` load

### Port Already in Use

**Problem**: Server says port is in use

**Solution**: The server automatically finds a free port. Just use the URL it provides.

### Components Not Loading

**Problem**: Sidebar or dashboard missing

**Solution**:
1. Check Flask route is serving templates:
   ```bash
   curl http://localhost:XXXX/templates/components/sidebar.html
   ```
2. Should return HTML content, not 404

### CSS Not Applied

**Problem**: Page has content but no styling

**Solution**:
1. Check CSS file loads:
   ```bash
   curl http://localhost:XXXX/static/css/style.css | head -20
   ```
2. Should show CSS rules starting with `* {`

## Testing Checklist

- [ ] Server starts without errors
- [ ] Homepage loads at `http://localhost:XXXX`
- [ ] Sidebar appears on the left
- [ ] Dashboard content is visible
- [ ] Navigation works (click different menu items)
- [ ] No errors in browser console
- [ ] CSS is applied (page looks styled, not plain HTML)

## Server Ports

The app tries these ports in order:
1. 5000 (default)
2. 5001
3. 5002
4. 5003
5. etc.

Always check the terminal output for the actual port being used.

## Development Mode

The server runs in debug mode by default:
- Auto-reloads on file changes
- Shows detailed error messages
- Debugger available

## Stop Server

Press `CTRL+C` in the terminal where the server is running.

## Need Help?

1. Check browser console for JavaScript errors
2. Check terminal for Python errors
3. Verify all files exist:
   ```bash
   ./verify_migration.sh
   ```
4. Test individual components:
   - Open `test_page.html` in browser
   - Check if components load there

---

**Quick Test**: Visit `http://localhost:XXXX/health` - should return `{"ok": true}`
