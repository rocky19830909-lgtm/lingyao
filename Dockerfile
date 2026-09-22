FROM public.ecr.aws/docker/library/node:22-alpine AS build
WORKDIR /app
RUN npm config set registry https://registry.npmmirror.com && npm install -g pnpm@10.10.0
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./
RUN pnpm config set registry https://registry.npmmirror.com && pnpm install --frozen-lockfile
COPY . .
ARG NEXT_PUBLIC_API_URL=/api
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN pnpm build

FROM public.ecr.aws/docker/library/node:22-alpine
WORKDIR /app
RUN npm config set registry https://registry.npmmirror.com && npm install -g pnpm@10.10.0
COPY --from=build /app ./
EXPOSE 3000
CMD ["pnpm","start","--host","0.0.0.0"]
