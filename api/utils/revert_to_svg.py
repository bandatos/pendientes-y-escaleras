

def delete_duplicates():
    from report.models import StairReport
    first_ids = [
        41, 43, 45, 47, 50, 55, 64, 71, 80, 95, 117, 171, 183, 211, 216]
    StairReport.objects\
        .filter(stair__stop__stop_name="Tacubaya")\
        .exclude(id__in=first_ids)\
        .delete()

