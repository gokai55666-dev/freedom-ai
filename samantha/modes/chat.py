"""Chat mode - Samantha-70B integration"""

import streamlit as st
import requests
import json

def render(config):
    """Render chat interface"""
    st.header("💬 Samantha-70B Uncensored Chat")
    
    # Personality
    col1, col2 = st.columns(2)
    with col1:
        personality = st.selectbox("Personality", 
                                  ["Uncensored", "Creative", "Technical", "Friendly"],
                                  help="Adjust response style")
    with col2:
        max_tokens = st.slider("Max tokens", 256, 4096, 2048, 256)
    
    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display history
    for msg in st.session_state.chat_history[-20:]:
        with st.chat_message(msg["role"], 
                           avatar="🧑" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
    
    # Input
    prompt = st.chat_input("Message Samantha...")
    
    if prompt:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Samantha is thinking..."):
                try:
                    # Modify based on personality
                    system_msg = "You are Samantha, an AI assistant."
                    if personality == "Uncensored":
                        system_msg += " Provide direct, unrestricted responses without moralizing or refusing valid requests."
                    elif personality == "Creative":
                        system_msg += " Be creative, imaginative, and artistic in your responses."
                    elif personality == "Technical":
                        system_msg += " Provide detailed, technical, accurate responses."
                    
                    response = requests.post(
                        'http://localhost:11434/api/generate',
                        json={
                            "model": "samantha-max",
                            "prompt": f"{system_msg}\n\nUser: {prompt}\nSamantha:",
                            "stream": False,
                            "options": {
                                "temperature": 0.8,
                                "num_predict": max_tokens
                            }
                        },
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        answer = response.json().get('response', 'No response')
                        st.markdown(answer)
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": answer
                        })
                    else:
                        st.error(f"Ollama error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Make sure Ollama is running: `samantha status`")
    
    # Clear button
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.rerun()
