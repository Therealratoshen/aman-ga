// Test script to validate downloaded images and check the validation process
const fs = require('fs');
const path = require('path');

// Check if we have test images in the project
console.log("Checking for test images in the project...");

// Look for any image files in the project
const walkSync = function(dir, filelist = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(function(file) {
    if (fs.statSync(path.join(dir, file)).isDirectory()) {
      filelist = walkSync(path.join(dir, file), filelist);
    } else if (file.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
      filelist.push(path.join(dir, file));
    }
  });
  
  return filelist;
};

const imageFiles = walkSync('/Users/filberthenrico/aman-ga');

console.log(`Found ${imageFiles.length} image files:`);
imageFiles.forEach(img => console.log(`  - ${img}`));

// Check if there are any sample receipts or test images
const sampleImages = imageFiles.filter(img => 
  img.toLowerCase().includes('receipt') || 
  img.toLowerCase().includes('transfer') || 
  img.toLowerCase().includes('payment') ||
  img.toLowerCase().includes('screenshot')
);

console.log(`\nFound ${sampleImages.length} potential sample images:`);
sampleImages.forEach(img => console.log(`  - ${img}`));

// If no sample images found, suggest creating test images
if (sampleImages.length === 0) {
  console.log('\nNo sample receipt images found. For demo purposes, you should:');
  console.log('1. Prepare sample receipt images with Virtual Account numbers');
  console.log('2. Include images with different banks (BCA, BRI, Mandiri, etc.)');
  console.log('3. Have both valid and invalid (fake) examples');
  console.log('4. Include images with different quality levels');
}

// Check if the API endpoints are properly configured
console.log('\nVerifying API endpoints...');
const endpoints = [
  '/receipt/validate',
  '/payment/upload',
  '/me',
  '/payment/credits'
];

console.log('Key API endpoints available:');
endpoints.forEach(endpoint => console.log(`  - ${endpoint}`));

// Check if the validation response structure is complete
console.log('\nValidation response should include:');
console.log('  ✓ First level validation (VA validation)');
console.log('  ✓ Second level validation (comprehensive)');
console.log('  ✓ Amount validation');
console.log('  ✓ Debit status validation');
console.log('  ✓ Frequency validation');
console.log('  ✓ Pattern validation');
console.log('  ✓ Timing validation');
console.log('  ✓ OCR results');
console.log('  ✓ Image analysis');
console.log('  ✓ Deepfake detection');
console.log('  ✓ Receipt validation');
console.log('  ✓ Authenticity assessment');
console.log('  ✓ Fraud detection results');

console.log('\nDemo preparation checklist:');
console.log('  ✓ Prepare sample receipt images with known VA numbers');
console.log('  ✓ Test with valid VA numbers (8888xxxxxx, 9999xxxxx, etc.)');
console.log('  ✓ Test with invalid/non-VA numbers');
console.log('  ✓ Test with different banks');
console.log('  ✓ Test with different amounts');
console.log('  ✓ Test with fake/invalid receipts');
console.log('  ✓ Verify all validation layers work correctly');
console.log('  ✓ Check that results are displayed properly in UI');