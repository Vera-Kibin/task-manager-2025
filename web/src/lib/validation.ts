import * as yup from "yup";
import type { Role, Status } from "./types";

export const NAME_RE = /^[\p{L}' -]{1,50}$/u;
export const NICK_RE = /^[A-Za-z0-9_-]{3,32}$/;
export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const userSchema = yup.object({
  id: yup.string().trim().required("id is required"),
  email: yup
    .string()
    .matches(EMAIL_RE, "invalid email")
    .required("email is required"),
  role: yup
    .mixed<Role>()
    .oneOf(["USER", "MANAGER"])
    .required("role is required"),
  status: yup
    .mixed<Status>()
    .oneOf(["ACTIVE", "BLOCKED"])
    .required("status is required"),
  first_name: yup
    .string()
    .matches(NAME_RE, "invalid first_name")
    .required("first_name is required"),
  last_name: yup
    .string()
    .matches(NAME_RE, "invalid last_name")
    .required("last_name is required"),
  nickname: yup
    .string()
    .matches(NICK_RE, "invalid nickname")
    .required("nickname is required"),
});
