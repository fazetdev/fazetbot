from utils.pdf_loader import load_pdf

text = load_pdf("/home/farukdev/Documents/fazet_corporate_profile.pdf")

print("\n--- PDF TEXT START ---\n")
print(text[:1500])
print("\n--- PDF TEXT END ---\n")

