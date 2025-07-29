document.addEventListener('DOMContentLoaded', function() {
    // Get form and elements
    const articleForm = document.getElementById('article-form');
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btn-text');
    const errorCard = document.getElementById('error-card');
    const errorMessage = document.getElementById('error-message');
    const urlTab = document.getElementById('url-tab');
    const pdfTab = document.getElementById('pdf-tab');
    const urlInput = document.getElementById('url');
    const pdfInput = document.getElementById('pdf_file');
    
    // Form submission handler
    if (articleForm) {
        articleForm.addEventListener('submit', function(event) {
            // Prevent default form submission temporarily for validation
            event.preventDefault();
            
            // Hide any previous errors
            if (errorCard) errorCard.classList.add('d-none');
            
            // Check which tab is active and validate accordingly
            const isUrlTabActive = urlTab && urlTab.classList.contains('active');
            const isPdfTabActive = pdfTab && pdfTab.classList.contains('active');
            
            // Default to URL tab if no tab is active or tabs don't exist
            const useUrlTab = isUrlTabActive || (!isUrlTabActive && !isPdfTabActive);
            
            let isValid = true;
            let errorMsg = '';
            
            if (isUrlTabActive || useUrlTab) {
                // Validate URL input
                if (!urlInput || !urlInput.value.trim()) {
                    isValid = false;
                    errorMsg = 'Please enter a URL';
                    if (urlInput) urlInput.classList.add('is-invalid');
                } else {
                    // URL validation
                    const urlPattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$/;
                    if (!urlPattern.test(urlInput.value)) {
                        isValid = false;
                        errorMsg = 'Please enter a valid URL';
                        urlInput.classList.add('is-invalid');
                    }
                }
            } else if (isPdfTabActive) {
                // Validate PDF input
                if (!pdfInput || !pdfInput.files || pdfInput.files.length === 0) {
                    isValid = false;
                    errorMsg = 'Please select a PDF file';
                    if (pdfInput) pdfInput.classList.add('is-invalid');
                } else {
                    // Check file type
                    const file = pdfInput.files[0];
                    if (!file.type.includes('pdf')) {
                        isValid = false;
                        errorMsg = 'The selected file is not a PDF';
                        pdfInput.classList.add('is-invalid');
                    } else if (file.size > 25 * 1024 * 1024) { // 25MB limit
                        isValid = false;
                        errorMsg = 'PDF file is too large (max 25MB)';
                        pdfInput.classList.add('is-invalid');
                    }
                }
            }
            
            if (!isValid) {
                // Show error
                showError(errorMsg);
                return;
            }
            
            // If validation passes, show loading state and submit the form
            submitBtn.disabled = true;
            spinner.classList.remove('d-none');
            btnText.textContent = 'Processing...';
            
            // Submit the form
            articleForm.submit();
        });
    }
    
    // Tab switching behavior
    if (urlTab && pdfTab) {
        urlTab.addEventListener('shown.bs.tab', function() {
            // Clear previous validation states
            if (urlInput) urlInput.classList.remove('is-invalid');
            if (pdfInput) pdfInput.classList.remove('is-invalid');
            if (errorCard) errorCard.classList.add('d-none');
        });
        
        pdfTab.addEventListener('shown.bs.tab', function() {
            // Clear previous validation states
            if (urlInput) urlInput.classList.remove('is-invalid');
            if (pdfInput) pdfInput.classList.remove('is-invalid');
            if (errorCard) errorCard.classList.add('d-none');
        });
    }
    
    // Handle errors
    function showError(message) {
        if (!errorCard || !errorMessage) {
            console.error('Error showing message:', message);
            return;
        }
        
        errorCard.classList.remove('d-none');
        errorMessage.textContent = message;
        
        // Reset button state
        if (submitBtn) submitBtn.disabled = false;
        if (spinner) spinner.classList.add('d-none');
        if (btnText) btnText.textContent = 'Summarize Content';
        
        // Scroll to error
        errorCard.scrollIntoView({ behavior: 'smooth' });
    }
    
    // URL validation on input
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            validateUrl(this);
        });
        
        urlInput.addEventListener('blur', function() {
            validateUrl(this);
        });
    }
    
    function validateUrl(input) {
        if (input.value.trim() === '') {
            input.classList.remove('is-valid', 'is-invalid');
            return;
        }
        
        // Simple URL validation
        const urlPattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$/;
        
        if (urlPattern.test(input.value)) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        }
    }
    
    // PDF file validation
    if (pdfInput) {
        pdfInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                const file = this.files[0];
                
                if (!file.type.includes('pdf')) {
                    this.classList.add('is-invalid');
                    showError('The selected file is not a PDF');
                } else if (file.size > 25 * 1024 * 1024) { // 25MB limit 
                    this.classList.add('is-invalid');
                    showError('PDF file is too large (max 25MB)');
                } else {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                    if (errorCard) errorCard.classList.add('d-none');
                }
            } else {
                this.classList.remove('is-valid', 'is-invalid');
            }
        });
    }
});
