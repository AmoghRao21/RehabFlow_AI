import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
    // Match all paths except Next.js internals and static files
    // This ensures /login, /signup etc. get redirected to /en/login, /en/signup
    matcher: ["/((?!_next|api|favicon\\.ico|images|.*\\..*).*)"],
};
