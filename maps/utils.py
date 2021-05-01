import math


def range_data(map_obj):
    """Helper function to range data"""
    data_range = []
    addition = 0

    if map_obj["data_min"] < float("Inf") and map_obj["data_max"] > -float("Inf"):
        red = {}
        green = {}
        blue = {}

        # Get value step
        if map_obj["logarithmic_scale"]:
            addition = 1 - map_obj["data_min"]
            step = math.log(map_obj["data_max"] + addition)
            step -= math.log(map_obj["data_min"] + addition)
            step /= map_obj["grades"]
        else:
            step = (map_obj["data_max"] - map_obj["data_min"]) / map_obj["grades"]

        # Convert colors to int
        red["start"] = int(map_obj["start_color"][:2], 16)
        green["start"] = int(map_obj["start_color"][2:4], 16)
        blue["start"] = int(map_obj["start_color"][4:], 16)

        red["end"] = int(map_obj["end_color"][:2], 16)
        green["end"] = int(map_obj["end_color"][2:4], 16)
        blue["end"] = int(map_obj["end_color"][4:], 16)

        # Get color steps
        red["step"] = (red["end"] - red["start"]) / map_obj["grades"]
        green["step"] = (green["end"] - green["start"]) / map_obj["grades"]
        blue["step"] = (blue["end"] - blue["start"]) / map_obj["grades"]

        for i in reversed(range(map_obj["grades"])):
            # Get current colors
            red["value"] = hex(red["start"] + int(red["step"] * i))[2:]
            green["value"] = hex(green["start"] + int(green["step"] * i))[2:]
            blue["value"] = hex(blue["start"] + int(blue["step"] * i))[2:]

            # Fix current colors (we need 2 digits)
            if len(red["value"]) != 2:
                red["value"] = "0" + red["value"]
            if len(green["value"]) != 2:
                green["value"] = "0" + green["value"]
            if len(blue["value"]) != 2:
                blue["value"] = "0" + blue["value"]

            if map_obj["logarithmic_scale"]:
                key = math.log(map_obj["data_max"] + addition) - step * (i + 1)
                key = math.pow(math.e, key)
                key -= addition
            else:
                key = map_obj["data_max"] - step * (i + 1)
            data_range.append([key, red["value"] + green["value"] + blue["value"]])

    return data_range
