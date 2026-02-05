# 🎨 Avatar System - Quick Visual Guide

## Gender-Based Color Schemes

### 👨 Male Avatar
```
Color: #4A90E2 (Professional Blue)
Use: Business, academic, professional contexts
Vibe: Trustworthy, calm, confident
```

### 👩 Female Avatar  
```
Color: #E91E63 (Vibrant Pink)
Use: Creative, energetic, friendly contexts
Vibe: Warm, approachable, dynamic
```

### 🌟 Other Avatar
```
Color: #9C27B0 (Creative Purple)
Use: Unique, artistic, individual expression
Vibe: Creative, inclusive, distinctive
```

### 🔒 Prefer Not to Say
```
Color: #667eea (Neutral Gradient)
Use: Privacy-focused, default option
Vibe: Neutral, inclusive, respectful
```

## Avatar Placements

### 1. Navigation Bar (Top Right)
```
Size: 35x35px
Border: 2px solid #667eea
Shadow: 0 2px 8px rgba(102, 126, 234, 0.3)
Hover: Scale 1.1, shadow increases
```

### 2. Profile Page (Main)
```
Size: 150x150px
Border: 5px solid #667eea
Shadow: 0 8px 24px rgba(102, 126, 234, 0.3)
Badge: Level indicator (bottom-right)
```

### 3. Room Creator (Cards)
```
Size: 28x28px
Border: 2px solid #667eea
Inline with username
```

### 4. Members List (Room)
```
Size: 32x32px
Border: 2px solid #667eea
Shadow: 0 2px 6px rgba(0, 0, 0, 0.1)
```

## CSS Classes Reference

### Avatar Classes
- `.user-avatar` - Navigation avatar
- `.profile-avatar` - Large profile avatar
- `.creator-avatar` - Room card creator avatar
- `.member-avatar` - Room member list avatar

### Gender Badge Classes
- `.gender-badge` - Base badge styling
- `.gender-male` - Blue gradient
- `.gender-female` - Pink gradient
- `.gender-other` - Purple gradient
- `.gender-prefer_not_to_say` - Default gradient

## Hover Effects

### All Avatars
```css
transition: transform 0.3s, box-shadow 0.3s;

:hover {
    transform: scale(1.1);
    box-shadow: increased;
}
```

### Navigation Avatar
```css
:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}
```

## Integration Examples

### Django Template Usage
```django
<!-- Basic avatar -->
<img src="{{ user.profile.get_avatar_url }}" alt="{{ user.username }}">

<!-- With all styling -->
<img src="{{ user.profile.get_avatar_url }}" 
     alt="{{ user.username }}" 
     class="user-avatar"
     title="{{ user.username }}'s avatar">

<!-- Gender badge -->
<span class="gender-badge gender-{{ profile.gender }}">
    {{ profile.get_gender_display }}
</span>
```

### Python Access
```python
# Get avatar URL
avatar_url = user.profile.get_avatar_url()

# Get gender
gender = user.profile.gender
gender_display = user.profile.get_gender_display()
```

## Form Implementation

### Signup Form
```python
gender = forms.ChoiceField(
    choices=[
        ('male', '👨 Male'),
        ('female', '👩 Female'),
        ('other', '🌟 Other'),
        ('prefer_not_to_say', '🔒 Prefer not to say'),
    ],
    widget=forms.Select(attrs={'class': 'form-control'})
)
```

### Profile Update
```python
fields = ['avatar', 'gender', 'bio', 'timezone']
```

## Responsive Breakpoints

### Mobile (< 768px)
- Navigation avatar: 30x30px
- Profile avatar: 120x120px
- Touch targets: Minimum 44x44px

### Tablet (768px - 1024px)
- Navigation avatar: 35x35px
- Profile avatar: 140x140px

### Desktop (> 1024px)
- Navigation avatar: 35x35px
- Profile avatar: 150x150px
- Member avatars: 32x32px

## Accessibility

### Alt Text
Always include descriptive alt text:
```django
alt="{{ user.username }}'s profile picture"
```

### Color Contrast
All gender badges maintain WCAG AA compliance:
- Text color: White (#ffffff)
- Background: High contrast gradients
- Minimum contrast ratio: 4.5:1

### Keyboard Navigation
- Avatars are focusable when interactive
- Clear focus indicators provided
- Screen reader friendly labels

## Performance Optimization

### Loading Strategy
1. Use `loading="lazy"` for below-fold avatars
2. Specify width/height to prevent layout shift
3. Consider WebP format for uploaded images

### Caching
```html
<!-- Browser caching -->
<img src="{{ avatar_url }}" 
     loading="lazy"
     decoding="async">
```

### CDN Usage
UI Avatars API provides:
- Global CDN delivery
- Automatic caching
- Fast response times

---

**This visual guide helps maintain consistency across the application!** 🎨
