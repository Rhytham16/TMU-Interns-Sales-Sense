import streamlit as st
import toml

def get_project_version():
    try:
        with open("pyproject.toml", "r") as toml_file:
            data = toml.load(toml_file)
        return data["project"]["version"]
    except Exception as e:
        return f"Error: {e}"

version = get_project_version()

st.title("About Us")

st.markdown("""
Founded in 2003, Cogent Infotech is a global, award-winning IT consulting firm headquartered in Pittsburgh, PA. With over two decades of experience, we specialize in delivering innovative digital transformation solutions to both commercial and public sector clients. Our services encompass Analytics, AI/ML, Application Development, Cloud Solutions, Cybersecurity, and more. We take pride in our long-standing partnerships with over 65 Fortune 500 companies and 70 government agencies, having successfully completed more than 10,000 projects. At Cogent, we are committed to excellence, fostering strong client relationships, and driving growth through cutting-edge technology and a dedicated team.

For more information, please visit our website: www.cogentinfo.com
""")

st.write(f"**App Version:** {version}")
