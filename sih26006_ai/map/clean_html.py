import re

path = r'd:\FREIGHT MODEL\sih26006_ai\map\freightselection.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# I want to remove the old HTML block and the old JS block.
# Let's find `<div class="modal-content">` and remove until `function closeVesselModal() { ... } </script>`

new_content = re.sub(r'<div class="modal-content">.*?</script>', '', content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
