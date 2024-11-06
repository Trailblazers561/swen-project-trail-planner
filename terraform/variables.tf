variable bucket_name {
  type = string
  default = "trailplanner-bucket"
}

variable bucket_acl {
  type        = string
  default     = "private"
  description = "Bucket ACL (Access Control Listing)"
}

variable react_app_directory {
  type        = string
  default     = "../swen-project-react-app"
}