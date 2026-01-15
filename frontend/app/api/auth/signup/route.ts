import { NextRequest, NextResponse } from "next/server"
import { hash } from "bcryptjs"
import { prisma } from "@/lib/prisma"

export async function POST(req: NextRequest) {
  try {
    const { name, email, password } = await req.json()

    // Validation
    if (!email || !password || !name) {
      return NextResponse.json(
        { error: "Tous les champs sont requis" },
        { status: 400 }
      )
    }

    // Check if user exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    })

    if (existingUser) {
      return NextResponse.json(
        { error: "Cet email est déjà utilisé" },
        { status: 400 }
      )
    }

    // Hash password
    const hashedPassword = await hash(password, 12)

    // Bootstrap logic: First user creates organization and becomes ADMIN
    const result = await prisma.$transaction(async (tx) => {
      // 1. Check if any organization exists (bootstrap check)
      const existingOrg = await tx.organization.findFirst()
      
      let organization
      let role: "ADMIN" | "MEMBER" = "MEMBER" // Default role for new users
      let isFirstUser = false

      if (!existingOrg) {
        // BOOTSTRAP: First user ever - create organization
        organization = await tx.organization.create({
          data: {
            name: "My Company",
            slug: "my-company",
            email: email,
          }
        })
        role = "ADMIN"
        isFirstUser = true
      } else {
        // Existing organization - new user joins as MEMBER
        organization = existingOrg
        role = "MEMBER"
      }

      // 2. Create user
      const user = await tx.user.create({
        data: {
          name,
          email,
          password: hashedPassword,
        }
      })

      // 3. Create membership
      await tx.membership.create({
        data: {
          userId: user.id,
          organizationId: organization.id,
          role: role,
          isOwner: isFirstUser,
        }
      })

      return { user, organization, role, isFirstUser }
    })

    return NextResponse.json(
      { 
        user: {
          id: result.user.id,
          name: result.user.name,
          email: result.user.email,
          role: result.role,
          isFirstUser: result.isFirstUser
        }
      },
      { status: 201 }
    )
  } catch (error) {
    console.error("Signup error:", error)
    return NextResponse.json(
      { error: "Une erreur est survenue lors de l'inscription" },
      { status: 500 }
    )
  }
}
