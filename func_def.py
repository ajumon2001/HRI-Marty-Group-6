from pydantic import BaseModel, Field
from typing import Optional, Union, Tuple, List

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
    color: Union[str, Tuple[int, int, int]] = Field(default="blue", description="Color for LEDs - 'white', 'red', 'blue', 'yellow', 'green', 'purple', etc. or RGB tuple")
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