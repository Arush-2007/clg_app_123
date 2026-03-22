-- CreateTable
CREATE TABLE "User" (
    "user_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "college" TEXT NOT NULL,
    "branch" TEXT NOT NULL,
    "year" INTEGER NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("user_id")
);

-- CreateTable
CREATE TABLE "Event" (
    "event_id" TEXT NOT NULL,
    "event_host" TEXT NOT NULL,
    "event_name" TEXT NOT NULL,
    "event_description" TEXT NOT NULL,
    "event_init_date" TIMESTAMP(3) NOT NULL,
    "event_end_date" TIMESTAMP(3) NOT NULL,
    "event_location" TEXT NOT NULL,
    "event_image_url" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Event_pkey" PRIMARY KEY ("event_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_user_id_key" ON "User"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
