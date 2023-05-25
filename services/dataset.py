from services.models import Procedure, Employee


def get_procedures():
    procedures = []
    for procedure in Procedure.objects.all():
        procedures.append(
            {
                'name': procedure.name,
                'cost': procedure.cost,
                'time': procedure.time,
            }
        )
    return procedures


def get_employees():
    employees = []
    for employee in Employee.objects.all():
        employees.append(
            {
                'name': employee.name,
                'phone': employee.phone,
                'position': employee.position,
            }
        )
    return employees

