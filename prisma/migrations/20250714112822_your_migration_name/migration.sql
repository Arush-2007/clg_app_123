/*
  Warnings:

  - Added the required column `event_video_url` to the `Event` table without a default value. This is not possible if the table is not empty.
  - Made the column `event_image_url` on table `Event` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE "Event" ADD COLUMN     "event_video_url" TEXT NOT NULL,
ALTER COLUMN "event_image_url" SET NOT NULL;
