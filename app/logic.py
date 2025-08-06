def generate_response(user_input, chat_history):
    user_messages = [m["text"] for m in chat_history if m["role"] == "user"]
    turn = len(user_messages)

    if turn == 1:
        return "Great! What kind of school subjects or classes have you enjoyed most?"
    elif turn == 2:
        return "Cool. Do you enjoy working with people, solving problems, creating things, or something else?"
    elif turn == 3:
        return "Nice. What do you value more — helping others, being creative, working independently, or building practical skills?"
    elif any(word in user_input.lower() for word in ["computer", "tech", "coding", "programming"]):
        return "Sounds like you’re into technology. You might explore Computer Science, IT Support, or Web Development. Would you like to see matching programs now or keep exploring?"
    elif any(word in user_input.lower() for word in ["health", "nurse", "doctor", "care"]):
        return "You seem drawn to helping people in healthcare. You might consider Nursing, Medical Assisting, or Public Health. Would you like to see matching programs now or keep exploring?"
    elif "show program" in user_input.lower():
        return "Here are some programs that match your interests:\n\n• **Computer Science**: 2-year degree with transfer to CSU\n• **IT Support**: Certificate in 9 months\n• **Web Development**: 1-year certificate with job placement support"
    elif "keep exploring" in user_input.lower():
        return "Great! Let's keep going. What kind of work environment sounds best — fast-paced, flexible, hands-on, or structured?"
    else:
        return "Thanks! I’m getting a sense of your interests. Would you like to see matching programs now or keep exploring?"