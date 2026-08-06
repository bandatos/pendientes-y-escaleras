from utils.clean_buckets import CleanBucket

x = CleanBucket(aws_location="escaleras/evidence_images", in_s3_by_csv=False)
x()
