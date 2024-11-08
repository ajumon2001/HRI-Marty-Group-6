# Standard library imports
import os
import sys
if sys.platform == 'win32':
    import msvcrt  # For Windows
import sys
if sys.platform != 'win32':
    import termios  # For Unix
    import tty     # For Unix

# Third-party imports

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from martypy import Marty
import time

# Local imports
from transcriber import transcribe_audio
from simple_recorder import record_audio
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Any
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AnyMessage, ToolMessage
# Load environment variables
load_dotenv()



BREAK_LOOP = False


from pydantic import BaseModel, Field
from typing import Optional, Union, Tuple, List


#These are Python classes defined using Pydantic, a data validation and settings management library in Python.
#Each class is designed to represent arguments for different actions that Marty the Robot can perform.

class MartyWalkArgs(BaseModel):
    """Arguments for making Marty walk forward"""
    num_steps: int = Field(default=4, description="Number of steps to take (1-10)")
    start_foot: str = Field(default="auto", description="Which foot to start with - 'left', 'right', or 'auto'")
    turn: int = Field(default=0, description="How much to turn (-100 to 100 degrees), 0 is straight")
    step_length: int = Field(default=40, description="How far to step (approximately in mm, 25-50 recommended)")
    move_time: int = Field(default=2000, description="How long each step should take in milliseconds")

class MartyDanceArgs(BaseModel):
    """Arguments for making Marty do a fun dance move"""
    side: str = Field(default="right", description="Which side to start dancing from - 'left' or 'right'")
    move_time: int = Field(default=4000, description="How long the dance should last in milliseconds (3000-5000 recommended)")

class MartyKickArgs(BaseModel):
    """Arguments for making Marty kick"""
    side: str = Field(default="right", description="Which foot to kick with - 'left' or 'right'")
    twist: int = Field(default=10, description="Amount of twisting to do while kicking (-30 to 30 degrees)")
    move_time: int = Field(default=3000, description="How long the kick should take in milliseconds")

class MartyLeanArgs(BaseModel):
    """Arguments for making Marty lean in a direction"""
    direction: str = Field(default="forward", description="Direction to lean - 'left', 'right', 'forward', or 'back'")
    amount: Optional[int] = Field(default=20, description="How much to lean - max 45° forward/back, max 60° left/right")
    move_time: int = Field(default=2000, description="How long the lean should take in milliseconds")

class MartyEyesArgs(BaseModel):
    """Arguments for changing Marty's eye expression"""
    pose_or_angle: Union[str, int] = Field(default="excited", description="Either a pose ('angry', 'excited', 'normal', 'wide', 'wiggle') or an angle in degrees")
    move_time: int = Field(default=1000, description="How long the eye movement should take in milliseconds")

class MartySidestepArgs(BaseModel):
    """Arguments for making Marty step sideways"""
    side: str = Field(default="left", description="Direction to step - 'left' or 'right'")
    steps: int = Field(default=2, description="Number of steps to take (1-5 recommended)")
    step_length: int = Field(default=30, description="How broad the steps are (25-50 recommended, max 127)")
    move_time: int = Field(default=2000, description="How long each step should take in milliseconds")

class MartyArmsArgs(BaseModel):
    """Arguments for moving Marty's arms"""
    left_angle: int = Field(default=50, description="Angle of the left arm (degrees -100 to 100, positive is up)")
    right_angle: int = Field(default=50, description="Position of the right arm (degrees -100 to 100, positive is up)")
    move_time: int = Field(default=2000, description="How long the arm movement should take in milliseconds")

class MartyMoveJointArgs(BaseModel):
    """Arguments for precisely moving a specific joint"""
    joint_name_or_num: Union[int, str] = Field(default="right arm", description="Joint to move - e.g. 'left hip', 'right knee', 'left arm', 'eyes'")
    position: int = Field(default=30, description="Angle in degrees to move the joint to (-100 to 100)")
    move_time: int = Field(default=2000, description="How long the movement should take in milliseconds")

class MartySpeakArgs(BaseModel):
    """Arguments for making Marty speak"""
    words: str = Field(default="Hello! I'm Marty!", description="What Marty should say")
    voice: str = Field(default="alto", description="Voice to use - 'alto' (normal), 'tenor' (lower), or 'chipmunk' (higher)")

class MartyDiscoColorArgs(BaseModel):
    """Arguments for controlling Marty's disco LED lights"""
    color: Union[str, Tuple[int, int, int]] = Field(default="red", description="Color for LEDs - 'white', 'red', 'blue', 'yellow', 'green', 'purple', etc. or RGB tuple")
    add_on: str = Field(default="eyes", description="Name of the disco add-on to control - typically 'eyes', 'feet', or 'arms'")
    region: Union[int, str] = Field(default="all", description="Region to light up - 'all' or specific region (0,1,2)")

class MartyCircleDanceArgs(BaseModel):
    """Arguments for making Marty do a circle dance"""
    side: str = Field(default="right", description="Which side to start on - 'left' or 'right'")
    move_time: int = Field(default=4000, description="How long the dance should take in milliseconds (3000-5000 recommended)")

class MartyWiggleArgs(BaseModel):
    """Arguments for making Marty do a wiggle movement"""
    move_time: int = Field(default=4000, description="How long the wiggle should take in milliseconds (3000-5000 recommended)")

class MartyCelebrateArgs(BaseModel):
    """Arguments for making Marty do a celebration movement"""
    move_time: int = Field(default=4000, description="How long the celebration should take in milliseconds (3000-5000 recommended)")

class MartyWaveArgs(BaseModel):
    """Arguments for making Marty wave"""
    side: str = Field(default="right", description="Which arm to wave with - 'left' or 'right'")

#Connection to my WIFI, Ajumon S22 Ultra as this is used to initialize and return an instance of Marty
def get_marty():
    """Initialize and return the Marty robot instance"""
    marty = Marty("wifi", "192.168.130.234")
    marty.set_blocking(True) #ensures commands send to the robot wait for completion before returning control to the program and makes it synchronous
    return marty

my_marty = get_marty()

#Base Model for Walking
class MartyArgs(BaseModel):
    """Arguments for the walk tool"""
    num_steps: int = Field(default=10, description="The number of steps Marty should walk if not specified")
    start_foot: str = Field(default="auto", description="The foot Marty should start with if not specified")
    step_length: int = Field(default=25, description="The length of each step Marty should take if not specified")
    move_time: int = Field(default=1500, description="The time it takes for Marty to move one step if not specified")

#These code snippets are collection of functions for controlling various actions.
@tool
def walk(walk_args: dict = {}):
    """Tool to tell Marty to walk forward
    
    Args:
        walk_args: A JSON object containing:
            num_steps (int): Number of steps to walk (default: 4)
            start_foot (str): Which foot to start with ('left', 'right', or 'auto') (default: 'auto')
            turn (int): How much to turn (-100 to 100 degrees) (default: 0)
            step_length (int): Length of each step in mm (default: 40)
            move_time (int): Time for each step in milliseconds (default: 2000)
    """
    args = MartyWalkArgs.model_validate(walk_args)
    print("EXECUTING WALK", args.model_dump())
    my_marty.walk(args.num_steps, args.start_foot, args.turn, args.step_length, args.move_time, True)
    return "NA"

@tool
def dance(dance_args: dict = {}):
    """Tool to make Marty do a fun dance move
    
    Args:
        dance_args: A JSON object containing:
            side (str): Which side to start dancing from ('left' or 'right') (default: 'right')
            move_time (int): How long the dance should last in milliseconds (default: 4000)
    """
    args = MartyDanceArgs.model_validate(dance_args)
    print("EXECUTING DANCE", args.model_dump())
    my_marty.dance(args.side, args.move_time, True)
    return "NA"

@tool
def kick(kick_args: dict = {}):
    """Tool to make Marty kick
    
    Args:
        kick_args: A JSON object containing:
            side (str): Which foot to kick with ('left' or 'right') (default: 'right')
            twist (int): Amount of twisting while kicking (-30 to 30 degrees) (default: 10)
            move_time (int): How long the kick should take in milliseconds (default: 3000)
    """
    args = MartyKickArgs.model_validate(kick_args)
    print("EXECUTING KICK", args.model_dump())
    my_marty.kick(args.side, args.twist, args.move_time, True)
    return "NA"

@tool
def lean(lean_args: dict = {}):
    """Tool to make Marty lean in a direction
    
    Args:
        lean_args: A JSON object containing:
            direction (str): Direction to lean ('left', 'right', 'forward', or 'back') (default: 'forward')
            amount (int): How much to lean (max 45° forward/back, max 60° left/right) (default: 20)
            move_time (int): How long the lean should take in milliseconds (default: 2000)
    """
    args = MartyLeanArgs.model_validate(lean_args)
    print("EXECUTING LEAN", args.model_dump())
    my_marty.lean(args.direction, args.amount, args.move_time, True)
    return "NA"

@tool
def eyes(eyes_args: dict = {}):
    """Tool to change Marty's eye expression
    
    Args:
        eyes_args: A JSON object containing:
            pose_or_angle: Either a pose ('angry', 'excited', 'normal', 'wide', 'wiggle') or angle in degrees (default: 'excited')
            move_time: How long the eye movement should take in milliseconds (default: 1000)
    """
    args = MartyEyesArgs.model_validate(eyes_args)
    print("EXECUTING EYES", args.model_dump())
    my_marty.eyes(args.pose_or_angle, args.move_time, True)
    return "NA"

@tool
def sidestep(sidestep_args: dict = {}):
    """Tool to make Marty step sideways
    
    Args:
        sidestep_args: A JSON object containing:
            side (str): Direction to step ('left' or 'right') (default: 'left')
            steps (int): Number of steps to take (1-5 recommended) (default: 2)
            step_length (int): How broad the steps are (25-50 recommended) (default: 30)
            move_time (int): How long each step should take in milliseconds (default: 2000)
    """
    args = MartySidestepArgs.model_validate(sidestep_args)
    print("EXECUTING SIDESTEP", args.model_dump())
    my_marty.sidestep(args.side, args.steps, args.step_length, args.move_time, True)
    return "NA"

@tool
def arms(arms_args: dict = {}):
    """Tool to move Marty's arms
    
    Args:
        arms_args: A JSON object containing:
            left_angle (int): Angle of left arm (-100 to 100, positive is up) (default: 50)
            right_angle (int): Angle of right arm (-100 to 100, positive is up) (default: 50)
            move_time (int): How long the movement should take in milliseconds (default: 2000)
    """
    args = MartyArmsArgs.model_validate(arms_args)
    print("EXECUTING ARMS", args.model_dump())
    my_marty.arms(args.left_angle, args.right_angle, args.move_time, True)
    return "NA"

@tool
def move_joint(joint_args: dict = {}):
    """Tool to precisely move a specific joint
    
    Args:
        joint_args: A JSON object containing:
            joint_name_or_num: Joint to move (e.g. 'left hip', 'right knee') (default: 'right arm')
            position (int): Angle in degrees (-100 to 100) (default: 30)
            move_time (int): How long the movement should take in milliseconds (default: 2000)
    """
    args = MartyMoveJointArgs.model_validate(joint_args)
    print("EXECUTING MOVE_JOINT", args.model_dump())
    my_marty.move_joint(args.joint_name_or_num, args.position, args.move_time, True)
    return "NA"

@tool
def speak(speak_args: dict = {}):
    """Tool to make Marty speak
    
    Args:
        speak_args: A JSON object containing:
            words (str): What Marty should say (default: "Hello! I'm Marty!")
            voice (str): Voice to use ('alto', 'tenor', 'chipmunk') (default: 'alto')
    """
    args = MartySpeakArgs.model_validate(speak_args)
    print("EXECUTING SPEAK", args.model_dump())
    my_marty.speak(args.words, args.voice, True)
    return "NA"

@tool
def disco_color(color: str = "green"):
    """Tool to control Marty's disco LED lights
    
    Args:
        disco_args: A JSON object containing:
            color: Color for LEDs ('white', 'red', 'blue', etc. or RGB tuple) (default: 'green')
            add_on: Name of disco add-on ('eyes', 'feet', 'arms') (default: 'eyes')
            region: Region to light up ('all' or 0,1,2) (default: 'all')
    """
    my_marty.set_blocking(True)
    # args = MartyDiscoColorArgs.model_validate(disco_args)
    # print("EXECUTING DISCO_COLOR", args.model_dump())
    my_marty.disco_color(color)
    return "NA"

@tool
def circle_dance(dance_args: dict = {}):
    """Tool to make Marty do a circle dance
    
    Args:
        dance_args: A JSON object containing:
            side (str): Which side to start on ('left' or 'right') (default: 'right')
            move_time (int): How long the dance should take in milliseconds (default: 4000)
    """
    args = MartyCircleDanceArgs.model_validate(dance_args)
    print("EXECUTING CIRCLE_DANCE", args.model_dump())
    my_marty.circle_dance(args.side, args.move_time, True)
    return "NA"

@tool
def wiggle(wiggle_args: dict = {}):
    """Tool to make Marty do a wiggle movement
    
    Args:
        wiggle_args: A JSON object containing:
            move_time (int): How long the wiggle should take in milliseconds (default: 4000)
    """
    args = MartyWiggleArgs.model_validate(wiggle_args)
    print("EXECUTING WIGGLE", args.model_dump())
    my_marty.wiggle(args.move_time, True)
    return "NA"

@tool
def celebrate(celebrate_args: dict = {}):
    """Tool to make Marty do a celebration movement
    
    Args:
        celebrate_args: A JSON object containing:
            move_time (int): How long the celebration should take in milliseconds (default: 4000)
    """
    args = MartyCelebrateArgs.model_validate(celebrate_args)
    print("EXECUTING CELEBRATE", args.model_dump())
    my_marty.celebrate(args.move_time, True)
    return "NA"

@tool
def wave(wave_args: dict = {}):
    """Tool to make Marty wave
    
    Args:
        wave_args: A JSON object containing:
            side (str): Which arm to wave with ('left' or 'right') (default: 'right')
    """
    args = MartyWaveArgs.model_validate(wave_args)
    print("EXECUTING WAVE", args.model_dump())
    my_marty.wave(args.side)
    return "NA"



@tool
def exit_program():
    """Tool to exit the program"""
    global BREAK_LOOP;
    BREAK_LOOP = True
    return "NA"


@tool
def walk(walk_args: MartyArgs = {}):
    """Tool to tell Marty to walk
    
    Args:
        args: A JSON object containing:
            num_steps (int): Number of steps to walk
            start_foot (str): Which foot to start with ('left' or 'right')
            step_length (int): Length of each step (0-100)
            move_time (int): Time for each step in milliseconds
    """
    args = MartyArgs.model_validate(walk_args)
    print("EXECUTING WALK", args)
    my_marty.walk(args.num_steps, args.start_foot, 0,  args.step_length, args.move_time, True)
    return "NA"

@tool
def get_ready():
    """Tool to tell Marty to get ready"""
    my_marty.get_ready()
    return "NA"



#MAIN EXECUTION FUNCTION OF THE PROGRAM
@tool
def select_color_and_tell_story():
    """When the user asks Marty to select a color and tell a story, this tool is used."""
    my_marty.get_ready()

    # Map color to emotion 
    
    color_to_emotion = {
        "red": "Adventure",
        "blue": "Magic",
        "green": "Adventure",
        "yellow": "Comedy",
        "purple": "Fantasy",
    }
    # speak_text("""Red means Adventure. Blue is for magic. Green is about Adventure. Yellow means Comedy. Purple is Fantasy""");
    my_marty.walk(num_steps=5, start_foot="auto", step_length=25, move_time=1500)
    my_marty.get_ready()
    story_chain = get_storyteller_chain()
    detected_color = my_marty.get_color_sensor_color("left")
    print("DETECTED COLOR", detected_color)
    story = story_chain.invoke({"emotion": color_to_emotion[detected_color] if detected_color in color_to_emotion else "neutral"})
    speak_text(story.content)
    return "celebrate"

#These are the Snippet codes for the Action of the Robot implemented in Tools
tools = [walk, get_ready, select_color_and_tell_story, exit_program, dance, kick, lean, eyes, circle_dance, disco_color, wiggle, celebrate, wave, arms, move_joint, sidestep, ]


#Storytelling Function
def get_storyteller_chain():
    """Initialize and return the storyteller chain"""
    # storyteller_model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    storyteller_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    storyteller_model = storyteller_model.bind_tools(tools)
    storyteller_template = ChatPromptTemplate.from_messages([
        ("system", "You are a story telling robot called Marty. Given the following genre, you need to tell a story that matches the genre. Keep the story short and concise. Break your conversations into length of 7."),
        ("user", "Please tell a story that matches the genre: {emotion}. Start the story directly as though you are speaking to a child as Marty. Use short sentences no more than 7 words.")
    ])
    return storyteller_template | storyteller_model


#Emotion Detection Function
def get_friendly_assistant():
    """Initialize and return the friendly assistant chain"""
    # assistant_model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    assistant_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    assistant_model = assistant_model.bind_tools(tools)
    # assistant_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    friendly_system_1 = "You are a friendly assistant called Marty. you should detect the emotion of the user based on how they interact. you have to comfort them and cheer them up using less than 20 words"
    system_2 = "You are a friendly assistant called Marty. Try and cheer them up. Use sentences that are less than 10 words. Short sentences. Use the tools provided to help them and follow their commands."
    assistant_template = ChatPromptTemplate.from_messages([
        ("system", system_2 ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}"),
    ])
    return assistant_template | assistant_model



# Initialize chains and robot functions which are the 2 primary Tasks
storyteller_chain = get_storyteller_chain()
friendly_assistant = get_friendly_assistant()

# my_marty = None

#Marty Speak is a Python Wrapper for its Functionality
def speak(text: str, blocking: bool = True, wait_less = False):
    """
    Wrapper function for Marty's speak functionality
    
    Args:
        text (str): The text to be spoken by Marty
        blocking (bool): Whether to wait for speech to complete before continuing
    """
    if my_marty:
        my_marty.speak_openai(text, blocking=blocking)
        # Sleep based on the length of the text. Fix approximately how long an average word is
        if not wait_less: #delay of 1 second
            time.sleep(1)

        # if wait_less:
        #     # time.sleep(len(text) * 0.01)
        #     pass
        # else:
        #     time.sleep(len(text) * 0.03)
    else:
        print(f"[Marty would say]: {text}")

#INITIAL START in Text to Speech
def greet():
    """Initial greeting when the program starts"""
    welcome_message = "Hello dear! I'm Marty, your robot friend. I'm ready to chat with you! how are you feeling today?"
    print(welcome_message)
    speak(welcome_message)

#It takes a long string of texts into smaller segments making it easier to read, process and display in parts.
def chunk_text(text: str, chunk_size: int = 7) -> list:
    """
    Split a long string into chunks of specified number of words.
    
    Args:
        text (str): The text to be chunked
        chunk_size (int): Number of words per chunk (default: 10)
        
    Returns:
        list: List of chunked strings
    """
    # Split text into words
    words = text.replace('!', '.').replace('?', '.').split('.')
    return words
    
    # Create chunks of specified size
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    
    # Join words in each chunk back into strings
    return [" ".join(chunk) for chunk in chunks]

def speak_text(text: str):
    """
    Speak text using Marty, chunking long text into smaller pieces.
    
    Args:
        text (str): The text to be spoken by Marty
    """
    # speak(text)
    # Split text into smaller chunks
    chunks = chunk_text(text)
    
    # # Speak each chunk
    for chunk in chunks:
        print(chunk)
        my_marty.set_blocking(True)
        speak(chunk, wait_less=True, blocking=False)
    my_marty.set_blocking(True)
 

#Provides a standardized way of Structuring the output of various tool function
class ToolResult(BaseModel):
    result: Any
    tool_name: str
    args: dict

def invoke_tools(tools, message: AnyMessage) -> list[ToolResult]:
    tools_by_name = {}
    results = []
    for tool in tools: 
        tools_by_name[tool.name] = tool
    for tool in message.tool_calls:
        name, args = tool['name'], tool['args']
        result = tools_by_name[name].invoke(args)
        results.append(ToolResult(result=result, tool_name=name, args=args))
    return results


messages = []

def conversational_flow():
    """Handle one conversation cycle"""
    print("Starting conversation flow")
    global messages;
    try:
        # Clean up previous recording
        if os.path.exists("recording.mp3"):
            os.remove("recording.mp3")
        
        if len(messages) > 12:
            messages = messages[-6:]
        
        print("Listening... (Recording for 10 seconds)")
        record_audio(duration=10)
        print("Recording complete")
        
        # Transcribe and generate response
        transcription = transcribe_audio("recording.mp3")
        print(transcription)
        if not transcription.strip():
            print("No speech detected, skipping...")
            return
            
        print("You said:", transcription)
        global BREAK_LOOP;
        # Get AI response and speak
        result = friendly_assistant.invoke({"question": transcription, "chat_history": messages})
        
        if result.tool_calls:
            tool_results = invoke_tools(tools, result)
            if tool_results:
                tool_result = tool_results[0]
                if tool_result.result  == "celebrate":
                    my_marty.celebrate()
                    time.sleep(1)
                    BREAK_LOOP = True
            print("Tool results:", tool_results)
        else:
            messages.append(result)
        # Speak the response
            speak_text(result.content)
        
    except Exception as e:
        print(f"Error in conversation flow: {e}")

def check_key_press():
    # Cross-platform key check
    if sys.platform == 'win32':
        # Windows
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            return key
    else:
        # Unix-based systems
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            if sys.stdin.read(1).lower() == 'q':
                return 'q'
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return None

def main():
    try:
        print("Program is running. Press 'q' to quit.")
        my_marty.set_volume(100)
        greet()
        global BREAK_LOOP;
        BREAK_LOOP = False
        
        while True and not BREAK_LOOP:
            print("Entered loop")
            # key = check_key_press()
            # if key == 'q':
            #     print("Quitting program...")
            #     break
            conversational_flow()
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Goodbye!")
        speak("Goodbye! It was nice talking to you! See you soon!")


















# def test():
#     story = """**The Starry Night Adventure**

# Once upon a time, in a small village nestled between rolling hills, there lived a curious little girl named Lila. Lila loved to gaze at the stars every night from her bedroom window. She often wondered what it would be like to visit them.

# One clear night, as Lila was counting the twinkling stars, she noticed a particularly bright one that seemed to be winking at her. Intrigued, she whispered, “I wish I could visit you, Star!” To her surprise, the star began to shimmer and sparkled even brighter. Suddenly, a soft, glowing light filled her room, and before she knew it, Lila was lifted gently into the air!

# She floated out of her window and soared high above the village, the cool night breeze brushing against her cheeks. The star, now glowing like a friendly lantern, guided her through the sky. They zipped past fluffy clouds and danced around the moon, which smiled down at them.

# “Where are we going?” Lila asked, her heart racing with excitement.

# “To the Land of Dreams!” the star replied in a cheerful voice. “It’s a magical place where dreams come to life!”

# As they arrived, Lila was amazed. The Land of Dreams was filled with colorful landscapes—fields of candy flowers, rivers of chocolate, and mountains made of fluffy marshmallows. Lila giggled with delight as she explored this enchanting world.

# She met a friendly dragon named Sparky, who loved to play hide-and-seek. They chased each other through the candy fields, and Lila even rode on Sparky’s back as he soared through the sky. They laughed and played until they stumbled upon a shimmering lake that sparkled like diamonds.

# “Let’s make a wish!” Lila suggested, and they both closed their eyes. Lila wished for all her friends in the village to experience this magical place.

# When she opened her eyes, the lake began to glow, and soon, her friends appeared, laughing and playing alongside her. They all enjoyed the wonders of the Land of Dreams together, sharing stories and creating memories that would last forever.

# As the night began to fade, the star gently reminded Lila, “It’s time to go home now, but you can always return in your dreams.”

# With a wave of her hand, Lila said goodbye to her friends and Sparky. The star wrapped her in its warm glow and flew her back to her bedroom window. As she settled back into her bed, Lila felt a sense of joy and wonder.

# From that night on, Lila knew that whenever she looked up at the stars, she could always find her way back to the Land of Dreams, where adventures awaited her.

# And with that comforting thought, Lila closed her eyes, drifting off to sleep with a smile on her face, ready for more adventures in her dreams.

# **The End.**

# Sweet dreams! 🌟"""
#     speak_text(story)



if __name__ == "__main__":
    main()
    # test()
    # speak_text("hello")
