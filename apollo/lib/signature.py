import copy
import inspect


def copy_parameters(from_signature, to_signature, parameter_keys):
    filtered_parameters = [
        to_signature.parameters[key] for key in
        to_signature.parameters if key not in parameter_keys
    ]

    new_parameters = bulk_create_new_parameters(
        filtered_parameters,
        [from_signature.parameters[key] for key in parameter_keys]
    )
    new_signature = to_signature.replace(parameters=new_parameters)
    return new_signature


def bulk_create_new_parameters(existing_parameters, new_parameters):
    parameters = existing_parameters
    for new_parameter in new_parameters:
        parameters = create_new_parameters(parameters, new_parameter)
    return parameters


def create_new_parameters(existing_parameters, new_parameter):
    if not existing_parameters:
        return [new_parameter]

    if check_parameter_has_default(new_parameter):
        new_parameters = copy.copy(existing_parameters)
        for i, parameter in enumerate(new_parameters):
            if check_parameter_has_default(parameter):
                new_parameters.insert(i, new_parameter)
                return new_parameters

            return existing_parameters + [new_parameter]
    else:
        return [new_parameter] + existing_parameters


def check_parameter_has_default(parameter):
    return parameter.default != inspect.Parameter.empty
