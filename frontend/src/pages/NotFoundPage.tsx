import { Link } from "react-router-dom";
import PageHeading from "../components/PageHeading";

export default function NotFoundPage() {
  return (
    <div className="space-y-6 text-center">
      <PageHeading title="Page not found" description="The page you are looking for does not exist." />
      <Link to="/" className="inline-flex items-center justify-center rounded-2xl bg-brand-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-brand-700">
        Return to dashboard
      </Link>
    </div>
  );
}
