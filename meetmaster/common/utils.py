def model_data_prop_was_changed(instance, validated_data, key):
    if key in validated_data:
        return getattr(instance, key) != validated_data[key]
    return False
