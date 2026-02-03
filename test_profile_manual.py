"""
Quick Profile Feature Test
This script tests profile functionality manually
"""
import sys
import os

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_test_result(test_name, status, message=""):
    """Print formatted test result"""
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{symbol} {test_name}")
    if message:
        print(f"   {message}")

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}PROFILE FEATURE MANUAL TEST CHECKLIST{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"{YELLOW}Server URL:{RESET} http://127.0.0.1:8000/\n")
    
    tests = [
        {
            "name": "Navigation Link",
            "url": "Check if 'Profile' link appears in navigation",
            "steps": [
                "1. Look at the navigation bar",
                "2. Verify 'Profile' link is visible between 'Progress' and 'Hi, username'"
            ]
        },
        {
            "name": "Profile Page Access",
            "url": "http://127.0.0.1:8000/profile/",
            "steps": [
                "1. Click on 'Profile' link or visit URL directly",
                "2. Verify page loads without errors",
                "3. Check if your username and avatar are displayed"
            ]
        },
        {
            "name": "Profile Stats Display",
            "url": "Same page as above",
            "steps": [
                "1. Verify 'Total Sessions' card shows correct count",
                "2. Check 'Minutes Studied' displays total time",
                "3. Verify 'Day Streak' shows current streak",
                "4. Check 'Current Level' displays your level"
            ]
        },
        {
            "name": "Profile Information",
            "url": "Same page as above",
            "steps": [
                "1. Verify email is displayed (only on your own profile)",
                "2. Check 'Joined' date is correct",
                "3. Verify 'Total XP' shows your experience points",
                "4. Check 'Timezone' displays correctly"
            ]
        },
        {
            "name": "Edit Profile Button",
            "url": "Same page as above",
            "steps": [
                "1. Look for 'Edit Profile' button",
                "2. Button should be purple gradient",
                "3. Click the button"
            ]
        },
        {
            "name": "Edit Profile Page",
            "url": "http://127.0.0.1:8000/profile/edit/",
            "steps": [
                "1. Verify edit page loads successfully",
                "2. Check avatar upload section is present",
                "3. Verify all form fields are populated with current data:",
                "   - Username",
                "   - Email",
                "   - First Name",
                "   - Last Name",
                "   - Bio",
                "   - Timezone"
            ]
        },
        {
            "name": "Avatar Upload",
            "url": "Same edit page",
            "steps": [
                "1. Click 'Choose Profile Picture' button",
                "2. Select an image file (JPG, PNG, GIF)",
                "3. Verify image preview appears",
                "4. Check file name is displayed",
                "5. Click 'Save Changes'"
            ]
        },
        {
            "name": "Form Validation",
            "url": "Same edit page",
            "steps": [
                "1. Try to clear username field and save",
                "2. Verify error message appears",
                "3. Try invalid email format",
                "4. Verify email validation works",
                "5. Try bio longer than 500 characters",
                "6. Verify character limit works"
            ]
        },
        {
            "name": "Update Profile",
            "url": "Same edit page",
            "steps": [
                "1. Update your bio with some text",
                "2. Change timezone",
                "3. Click 'Save Changes'",
                "4. Verify redirect to profile page",
                "5. Check success message appears",
                "6. Verify changes are saved and displayed"
            ]
        },
        {
            "name": "Avatar Display",
            "url": "http://127.0.0.1:8000/profile/",
            "steps": [
                "1. Return to profile page",
                "2. Verify uploaded avatar is displayed",
                "3. Check avatar is circular (120px)",
                "4. Verify avatar has purple border"
            ]
        },
        {
            "name": "View Other User's Profile",
            "url": "http://127.0.0.1:8000/profile/<other_username>/",
            "steps": [
                "1. Visit another user's profile (replace <other_username>)",
                "2. Verify profile displays correctly",
                "3. Check 'Edit Profile' button is NOT visible",
                "4. Verify email is NOT displayed for other users"
            ]
        },
        {
            "name": "API Endpoint - GET",
            "url": "http://127.0.0.1:8000/api/profile/",
            "steps": [
                "1. Open URL in browser or use curl:",
                "   curl http://127.0.0.1:8000/api/profile/",
                "2. Verify JSON response with user data",
                "3. Check response includes:",
                "   - user (username, email, first_name, last_name)",
                "   - profile (avatar_url, bio, timezone)",
                "   - stats (total_study_minutes, study_streak, level, total_xp)"
            ]
        },
        {
            "name": "Responsive Design",
            "url": "Profile and edit pages",
            "steps": [
                "1. Resize browser window to mobile size",
                "2. Verify profile cards stack vertically",
                "3. Check edit form adapts to narrow screen",
                "4. Verify all elements remain accessible"
            ]
        },
        {
            "name": "Dark Theme Compatibility",
            "url": "All profile pages",
            "steps": [
                "1. Toggle dark theme (moon icon)",
                "2. Visit profile page",
                "3. Verify colors adapt properly",
                "4. Check text is readable",
                "5. Visit edit page and verify form visibility"
            ]
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{GREEN}Test {i}: {test['name']}{RESET}")
        print(f"{YELLOW}URL:{RESET} {test['url']}")
        print(f"{YELLOW}Steps:{RESET}")
        for step in test['steps']:
            print(f"  {step}")
        print()
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}ADDITIONAL CHECKS{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"{GREEN}File Upload Validation:{RESET}")
    print("  • Try uploading file > 2MB (should show error)")
    print("  • Try uploading non-image file (should show error)")
    print("  • Verify error messages are clear\n")
    
    print(f"{GREEN}Username Uniqueness:{RESET}")
    print("  • Try changing username to existing user")
    print("  • Verify error message appears")
    print("  • Keep your original username\n")
    
    print(f"{GREEN}Session Data:{RESET}")
    print("  • Complete a study session")
    print("  • Return to profile")
    print("  • Verify stats update (Total Sessions, Minutes)")
    print("  • Check 'Recent Activity' shows last 7 days\n")
    
    print(f"{GREEN}Error Handling:{RESET}")
    print("  • Visit /profile/nonexistent_user/")
    print("  • Verify 404 page or appropriate error")
    print("  • Try accessing profile while logged out")
    print("  • Verify redirect to login page\n")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}EXPECTED RESULTS{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"{GREEN}✓{RESET} All pages load without 500 errors")
    print(f"{GREEN}✓{RESET} Profile displays user information correctly")
    print(f"{GREEN}✓{RESET} Stats show accurate study session data")
    print(f"{GREEN}✓{RESET} Edit form updates profile successfully")
    print(f"{GREEN}✓{RESET} Avatar upload works with validation")
    print(f"{GREEN}✓{RESET} Form validation prevents invalid data")
    print(f"{GREEN}✓{RESET} Success messages appear after save")
    print(f"{GREEN}✓{RESET} Responsive design works on all screen sizes")
    print(f"{GREEN}✓{RESET} Dark theme displays correctly")
    print(f"{GREEN}✓{RESET} Other users' profiles viewable but not editable")
    print(f"{GREEN}✓{RESET} API endpoints return proper JSON")
    print(f"{GREEN}✓{RESET} Navigation includes Profile link\n")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Note:{RESET} Mark each test as PASS or FAIL as you complete it")
    print(f"{YELLOW}Tip:{RESET} Open browser DevTools (F12) to check for console errors")
    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == '__main__':
    main()
