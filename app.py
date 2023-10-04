import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from utils import image_interface
import streamlit as st
from streamlit_image_select import image_select
from dotenv import load_dotenv      

load_dotenv()

# Access the AUTH_TOKEN environment variable
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Create headers with Authorization
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
st.set_page_config(page_title="Image Similarity", page_icon=" ")
IMAGE_SIMILARITY_DEMO = "https://abhilashvj-computer-vision-backend.hf.space/find-similar-image-pinecone/"
# IMAGE_SIMILARITY_DEMO = "http://127.0.0.1:8000/find-similar-image-pinecone/"
TMP_DIR = "./tmp"

os.makedirs(TMP_DIR, exist_ok=True)

def similar_images(im, action, image_list, top_k=5, namespace="av_local", model="huggingface"):
    # g = size / max(im.size)  # gain
    # im = im.resize((int(x * g) for x in im.size), Image.ANTIALIAS)  # resize
    if action == "delete":
        test_files = []        
        response = requests.post(f"{IMAGE_SIMILARITY_DEMO}?top_k={top_k}&namespace={namespace}&model={selected_model}", files=test_files, headers=headers)                                           
        if response.status_code == 200:
            return [],["Deleting namespace successfull"]
        else:
            return [],["Deleting namespace Failed"]
            
    elif action =="query":
        query_filepath = im.name
        im = Image.open(im)
        im.save(f"{TMP_DIR}/{query_filepath}")
        query_image = [f"{TMP_DIR}/{query_filepath}" ]
        test_files = [  ("query_image", open(f, 'rb')) for f in  query_image]
        response = requests.post(f"{IMAGE_SIMILARITY_DEMO}?top_k={top_k}&namespace={namespace}", files=test_files, headers=headers)
        images = []
        texts = []
        if response.status_code == 200:
            for im in response.json()['similar_images']:
                texts.append(f"{im['filename']} :{im['score']}")
                try:
                    im = Image.open(BytesIO(base64.b64decode(im['encoded_img'])))
                    images.append(im)
                except:
                    images.append(None)
                

        return images, texts

    elif action == "index":

        collection_of_images = []
        for im in image_list:
            file_path = f"{TMP_DIR}/{im.name}"
            print(f"saving image at: {file_path}")
            im = Image.open(im)
            im.save(file_path)
            collection_of_images.append(file_path)
        
        test_files = [  ("images_to_search", open(f, 'rb')) for f in collection_of_images ]
        
        response = requests.post(f"{IMAGE_SIMILARITY_DEMO}?action=index&namespace={namespace}", files=test_files,headers=headers)                                                  
        if response.status_code == 200:
            return [],["Indexing successfull"]
        else:
            return [],["Indexing Failed"]
    
    return [], []

     
# query_image = image_select("Label", ["gas-distribution-piping25.jpg", "gas-distribution-regulator9.jpeg", "gas-distribution-valves28.jpg", 
# "gas-distribution-valves29.jpg", "Cars101.png", "Cars100.png"]) 
namespace = st.text_input('vector DB Namespace', 'av_local')
models = ["huggingface", "sentence_transformers"]  # Add the list of available models here
selected_model = st.selectbox("Select a model", models)
run_pressed = st.button("Delete Previous Index")
if run_pressed:
    similar_images(None, "delete", [], top_k=5, namespace="av_local")
    st.write(f"Deleted the previous indexed images &nbsp;&nbsp; ")
    
query_image = st.file_uploader("Select the Query Image", type=["jpg", "jpeg", "png", "JPG", "PNG", "JPEG"])
images_to_search = st.file_uploader("Select the Images to Index", type=["jpg", "jpeg", "png", "JPG", "PNG", "JPEG"],  accept_multiple_files=True)
selected_option = st.radio(
"Set the action type ",
# key="visibility",
options=["query", "index"],
)
top_k = 1
# st.image(images_to_search, use_column_width=True)
#Add 'before' and 'after' columns
if selected_option == "index":
    search = st.button('Index Images')
if selected_option == "query":
    search = st.button('Find Similar')

    top_k = st.number_input('Insert number of images to retrieve', min_value=1, max_value=10,step=1, value=3 )

if ((query_image is not None) or (images_to_search is not None)) and (search):
    
    col1, col2 = st.columns( [0.2, 0.8])
    with col1:
        st.markdown('<p style="text-align: center;">Uplaoded File</p>',unsafe_allow_html=True)
        if selected_option == "query":
            st.image(Image.open(query_image), caption=f"Query image: {query_image.name}")
        if selected_option == "index":
            st.image(images_to_search, caption=[im.name for im in images_to_search])
        # image_select("Images to search",images_to_search)

    with col2:
        st.markdown('<p style="text-align: center;">Result File</p>',unsafe_allow_html=True)
        images, titles = similar_images(query_image, selected_option, images_to_search, top_k=top_k, namespace=namespace, model=selected_model)
        if selected_option == "query":
            try:
                st.image(images, caption=titles)
            except:
                st.write(titles)
        if selected_option == "index":
            st.write( titles[0])
        # image_select("Top similar images",images)

        # st.image(result_image,caption=title,use_column_width="always")



