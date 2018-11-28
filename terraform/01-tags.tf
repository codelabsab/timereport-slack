//  Wherever possible, we will use a common set of tags for resources. This
//  makes it much easier to set up resource based billing, tag based access,
//  resource groups and more.
//
//  This is quite fiddly, the following resources should be useful:
//
//    - Terraform: Local Values: https://www.terraform.io/docs/configuration/locals.html
//    - Terraform: Default Tags for Resources in Terraform: https://github.com/hashicorp/terraform/issues/2283
//    - Terraform: Variable Interpolation for Tags: https://github.com/hashicorp/terraform/issues/14516

//  Define our common tags.
//   - Project: Purely for my own organision, delete or change as you like!
//  The syntax below is ugly, but needed as we are using dynamic key names.
locals {
  common_tags = "${map(
    "Name", "slack-api-prod",
    "Owner", "terraform",
    "Purpose", "slack"
  )}"
}
