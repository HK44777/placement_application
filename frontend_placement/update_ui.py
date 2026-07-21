import os, re

vue_files = []
for root, _, files in os.walk('src/views'):
    for f in files:
        if f.endswith('.vue'):
            vue_files.append(os.path.join(root, f))

for file_path in vue_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove standard error message divs
    content = re.sub(r'<div v-if="errorMessages\.length > 0".*?</div>', '', content, flags=re.DOTALL)
    # Remove standard success message divs
    content = re.sub(r'<div v-if="successMessage".*?</div>', '', content, flags=re.DOTALL)
    
    # Replace error pushing with toast
    content = re.sub(r'errorMessages\.value\.push\((.*?)\)', r'toast.error(\1)', content)
    
    # Replace success message setting with toast
    content = re.sub(r'successMessage\.value\s*=\s*(.*?)\n', r'toast.success(\1)\n', content)
    
    # Replace btn-dark with btn-primary for consistent look
    content = content.replace('btn-dark', 'btn-primary')
    
    # If toast is used but not imported, add it
    if 'toast.' in content and 'import { toast }' not in content:
        content = re.sub(r'</script>', r"import { toast } from 'vue3-toastify'\n</script>", content, flags=re.DOTALL)
        content = re.sub(r'(import .*? from .*?\n)', r"\1import { toast } from 'vue3-toastify'\n", content, count=1)
        
    if original != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('Updated files.')
