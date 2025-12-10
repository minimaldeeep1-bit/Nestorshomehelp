const fs = require('fs');
const assert = require('assert');

try {
  // Read the contents of the HTML files
  const okotoksContent = fs.readFileSync('okotoks-handyman.html', 'utf-8');
  const airdrieContent = fs.readFileSync('airdrie-handyman.html', 'utf-8');

  // Helper function to normalize and check for substring
  const assertContent = (content, substring, errorMessage) => {
    const normalizedContent = content.replace(/\s+/g, ' ').trim();
    const normalizedSubstring = substring.replace(/\s+/g, ' ').trim();
    assert(normalizedContent.includes(normalizedSubstring), errorMessage);
  };

  // Test cases for okotoks-handyman.html
  assertContent(okotoksContent, '<title>Okotoks Handyman Services', 'Okotoks title is incorrect.');
  assertContent(okotoksContent, 'Your Handyman in <span class="text-orange">Okotoks</span>', 'Okotoks H1 is incorrect.');
  assertContent(okotoksContent, '<input type="hidden" name="location_source" value="Okotoks Landing Page">', 'Okotoks form value is incorrect.');
  assert(!okotoksContent.includes('Airdrie'), 'Okotoks page should not contain "Airdrie".');

  // Test cases for airdrie-handyman.html
  assertContent(airdrieContent, '<title>Airdrie Handyman Services', 'Airdrie title is incorrect.');
  assertContent(airdrieContent, 'Your Handyman in <span class="text-orange">Airdrie</span>', 'Airdrie H1 is incorrect.');
  assertContent(airdrieContent, '<input type="hidden" name="location_source" value="Airdrie Landing Page">', 'Airdrie form value is incorrect.');
  assert(!airdrieContent.includes('Okotoks'), 'Airdrie page should not contain "Okotoks".');

  console.log('All tests passed!');
} catch (error) {
  console.error('Test failed:', error.message);
  process.exit(1);
}
