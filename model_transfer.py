import joblib
import pathlib
import pickle

# Custom unpickler to handle WindowsPath objects
class WindowsPathUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "pathlib" and name == "WindowsPath":
            return pathlib.PosixPath  # Replace WindowsPath with PosixPath for compatibility
        return super().find_class(module, name)

def load_with_compatibility(filepath):
    with open(filepath, "rb") as f:
        return WindowsPathUnpickler(f).load()

# Load the problematic file
old_model_path = "ift6758/ift6758/models/LogisticReg_Distance_Angle.pkl"
model = load_with_compatibility(old_model_path)

# Save it again in a Linux-compatible format
new_model_path = "ift6758/ift6758/models/LogisticReg_Distance_Angle_new.pkl"
joblib.dump(model, new_model_path)
print(f"Model re-saved to {new_model_path} in a compatible format.")
