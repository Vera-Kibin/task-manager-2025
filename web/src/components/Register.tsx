import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { register as doRegister, setActorId } from "../lib/api";

const Schema = Yup.object({
  first_name: Yup.string().min(2).max(50).required("Required"),
  last_name: Yup.string().min(2).max(50).required("Required"),
  nickname: Yup.string()
    .matches(/^[A-Za-z0-9_-]{3,32}$/, "3–32 zn., litery/cyfry/_/-")
    .required("Required"),
  email: Yup.string().email().required("Required"),
});

export default function Register({ onDone }: { onDone: () => void }) {
  return (
    <Formik
      initialValues={{ first_name: "", last_name: "", nickname: "", email: "" }}
      validationSchema={Schema}
      onSubmit={async (values, { setSubmitting, setStatus }) => {
        try {
          const out = await doRegister(values);
          localStorage.setItem("nickname", values.nickname);
          setActorId(out.id);
          onDone();
        } catch (e: any) {
          setStatus(e.message);
        } finally {
          setSubmitting(false);
        }
      }}
    >
      {({ isSubmitting, status }) => (
        <Form className="space-y-4">
          <h2 className="text-xl font-semibold">Create your account</h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="flex flex-col">
              <span>First name</span>
              <Field name="first_name" className="input" />
              <ErrorMessage
                name="first_name"
                component="span"
                className="text-rose-600 text-sm"
              />
            </label>
            <label className="flex flex-col">
              <span>Last name</span>
              <Field name="last_name" className="input" />
              <ErrorMessage
                name="last_name"
                component="span"
                className="text-rose-600 text-sm"
              />
            </label>
            <label className="flex flex-col md:col-span-2">
              <span>Nickname</span>
              <Field name="nickname" className="input" />
              <ErrorMessage
                name="nickname"
                component="span"
                className="text-rose-600 text-sm"
              />
            </label>
            <label className="flex flex-col md:col-span-2">
              <span>Email</span>
              <Field type="email" name="email" className="input" />
              <ErrorMessage
                name="email"
                component="span"
                className="text-rose-600 text-sm"
              />
            </label>
          </div>

          <button
            className="btn btn-solid-black btn-lg w-full"
            disabled={isSubmitting}
          >
            Register
          </button>
          {status && <div className="text-rose-600">{status}</div>}
        </Form>
      )}
    </Formik>
  );
}
