import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { login as doLogin, setActorId } from "../lib/api";

const Schema = Yup.object({
  email: Yup.string().email().required("Required"),
  nickname: Yup.string()
    .matches(/^[A-Za-z0-9_-]{3,32}$/)
    .required("Required"),
});

export default function Login({ onDone }: { onDone: () => void }) {
  return (
    <Formik
      initialValues={{ email: "", nickname: "" }}
      validationSchema={Schema}
      onSubmit={async (vals, { setStatus, setSubmitting }) => {
        try {
          const out = await doLogin(vals);
          setActorId(out.id);
          localStorage.setItem("nickname", out.nickname || vals.nickname);
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
          <h2 className="text-xl font-semibold">Sign in</h2>

          <label className="flex flex-col">
            <span>Email</span>
            <Field type="email" name="email" className="input" />
            <ErrorMessage
              name="email"
              component="span"
              className="text-rose-600 text-sm"
            />
          </label>

          <label className="flex flex-col">
            <span>Nickname</span>
            <Field name="nickname" className="input" />
            <ErrorMessage
              name="nickname"
              component="span"
              className="text-rose-600 text-sm"
            />
          </label>

          <button
            className="btn btn-solid-black btn-lg w-full"
            disabled={isSubmitting}
          >
            Log in
          </button>
          {status && <div className="text-rose-600">{status}</div>}
        </Form>
      )}
    </Formik>
  );
}
